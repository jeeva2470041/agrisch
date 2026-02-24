import 'package:flutter/material.dart';
import '../models/scheme_model.dart';
import '../services/api_service.dart';
import '../l10n/app_localizations.dart';

/// A simple chat message model.
class _ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;

  _ChatMessage({
    required this.text,
    required this.isUser,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

/// AI Chat Screen — allows farmers to ask questions about a specific scheme
/// and get AI-powered answers.
class AskAiScreen extends StatefulWidget {
  final SchemeModel scheme;
  const AskAiScreen({super.key, required this.scheme});

  @override
  State<AskAiScreen> createState() => _AskAiScreenState();
}

class _AskAiScreenState extends State<AskAiScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final _apiService = ApiService();
  final List<_ChatMessage> _messages = [];
  bool _isLoading = false;

  static const _primary = Color(0xFF2E7D32);

  /// Build a context string from the scheme for AI.
  String get _schemeContext {
    final s = widget.scheme;
    return 'Scheme Name: ${s.name}\n'
        'Type: ${s.type}\n'
        'Benefit: ${s.benefit}\n'
        'States: ${s.states.join(', ')}\n'
        'Crops: ${s.crops.join(', ')}\n'
        'Land Range: ${s.minLand} - ${s.maxLand} hectares\n'
        'Season: ${s.season}\n'
        'Documents Required: ${s.documentsRequired.join(', ')}\n'
        'Official Link: ${s.officialLink}\n'
        'Description: ${s.getDescription('en')}';
  }

  @override
  void initState() {
    super.initState();
    // Add a welcome message
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final l = AppLocalizations.of(context);
      setState(() {
        _messages.add(_ChatMessage(
          text: '${l.askAiWelcome} "${widget.scheme.name}". ${l.askAiPrompt}',
          isUser: false,
        ));
      });
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage() async {
    final question = _controller.text.trim();
    if (question.isEmpty || _isLoading) return;

    _controller.clear();

    setState(() {
      _messages.add(_ChatMessage(text: question, isUser: true));
      _isLoading = true;
    });
    _scrollToBottom();

    final localeCode = Localizations.localeOf(context).languageCode;

    final answer = await _apiService.askAi(
      question: question,
      schemeContext: _schemeContext,
      language: localeCode,
    );

    if (mounted) {
      setState(() {
        _messages.add(_ChatMessage(text: answer, isUser: false));
        _isLoading = false;
      });
      _scrollToBottom();
    }
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l.askAi),
        backgroundColor: _primary,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Column(
        children: [
          // Scheme chip at the top
          _buildSchemeHeader(),

          // Chat messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length && _isLoading) {
                  return _buildTypingIndicator();
                }
                return _buildMessageBubble(_messages[index]);
              },
            ),
          ),

          // Suggestion chips (shown when no user messages yet)
          if (_messages.length <= 1) _buildSuggestionChips(l),

          // Input bar
          _buildInputBar(l),
        ],
      ),
    );
  }

  Widget _buildSchemeHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: _primary.withValues(alpha: 0.08),
        border: Border(
          bottom: BorderSide(color: _primary.withValues(alpha: 0.15)),
        ),
      ),
      child: Row(
        children: [
          Icon(Icons.policy, color: _primary, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              widget.scheme.name,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: _primary,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(_ChatMessage message) {
    final isUser = message.isUser;
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.only(
          bottom: 10,
          left: isUser ? 48 : 0,
          right: isUser ? 0 : 48,
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isUser ? _primary : Colors.grey.shade100,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 16),
          ),
        ),
        child: isUser
            ? Text(
                message.text,
                style: const TextStyle(color: Colors.white, fontSize: 15),
              )
            : SelectableText(
                message.text,
                style: TextStyle(
                  color: Colors.grey.shade800,
                  fontSize: 15,
                  height: 1.5,
                ),
              ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10, right: 48),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: Colors.grey.shade100,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(16),
            topRight: Radius.circular(16),
            bottomRight: Radius.circular(16),
            bottomLeft: Radius.circular(4),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: _primary,
              ),
            ),
            const SizedBox(width: 10),
            Text(
              'Thinking...',
              style: TextStyle(color: Colors.grey.shade600, fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionChips(AppLocalizations l) {
    final suggestions = [
      l.askAiSuggestion1,
      l.askAiSuggestion2,
      l.askAiSuggestion3,
    ];

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: suggestions.map((suggestion) {
          return ActionChip(
            label: Text(
              suggestion,
              style: TextStyle(fontSize: 13, color: _primary),
            ),
            backgroundColor: _primary.withValues(alpha: 0.08),
            side: BorderSide(color: _primary.withValues(alpha: 0.2)),
            onPressed: () {
              _controller.text = suggestion;
              _sendMessage();
            },
          );
        }).toList(),
      ),
    );
  }

  Widget _buildInputBar(AppLocalizations l) {
    return Container(
      padding: EdgeInsets.only(
        left: 12,
        right: 8,
        top: 8,
        bottom: MediaQuery.of(context).padding.bottom + 8,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              textInputAction: TextInputAction.send,
              maxLines: 3,
              minLines: 1,
              onSubmitted: (_) => _sendMessage(),
              decoration: InputDecoration(
                hintText: l.askAiHint,
                hintStyle: TextStyle(color: Colors.grey.shade400),
                filled: true,
                fillColor: Colors.grey.shade100,
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Material(
            color: _isLoading ? Colors.grey : _primary,
            borderRadius: BorderRadius.circular(24),
            child: InkWell(
              borderRadius: BorderRadius.circular(24),
              onTap: _isLoading ? null : _sendMessage,
              child: const Padding(
                padding: EdgeInsets.all(10),
                child: Icon(Icons.send_rounded, color: Colors.white, size: 22),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
